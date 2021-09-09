import React, { Component } from 'react';
import PropTypes from 'prop-types';
import Immutable from 'immutable';

class AuthorHighlights extends Component {
  render() {
    const { renderItem, results } = this.props;
    return (
      <div data-test-id="author-highlight-results">
        {results.map((result) => (
          <div className="mv2" key={result.get('id')}>
            {renderItem(result)}
          </div>
        ))}
      </div>
    );
  }
}

AuthorHighlights.propTypes = {
  results: PropTypes.instanceOf(Immutable.List),
  renderItem: PropTypes.func.isRequired,
};

AuthorHighlights.defaultProps = {
  results: Immutable.List(),
};

export default AuthorHighlights;
